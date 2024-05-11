# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    DialogTurnStatus
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    AttachmentPrompt,
    PromptOptions,
    PromptValidatorContext,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState
import os
import json
# connection_string = os.environ.get("COSMOS_DB_CONNECTION_STRING","")
connection_string = 'AccountEndpoint={"code":"BadRequest","message":"Request url is invalid.\r\nActivityId: 37341adf-2268-433f-b95e-aa858758339b, Windows/10.0.20348 cosmos-netstandard-sdk/3.18.0"}'
from data_models import UserProfile
from .text_processor import TextProcessor
from .query_db import CosmosDBQuery

class UserProfileDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(UserProfileDialog, self).__init__(UserProfileDialog.__name__)

        self.user_profile_accessor = user_state.create_property("UserProfile")

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.podcast_step,
                    self.query_step,
                    self.confirm_step,
                    self.summary_step,
                    self.handle_query_again,
                    self.final_step
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        
        self.initial_dialog_id = WaterfallDialog.__name__

    async def podcast_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.context.activity.text == "@search":
            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("請選擇你有興趣查詢的Podcast節目~"),
                    choices=[Choice("好味小姐"), Choice("唐陽雞酒屋"), Choice("股癌")],
                )
            )
        else:
            return DialogTurnResult(DialogTurnStatus.Complete)

    async def query_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        podcast = step_context.result.value
        step_context.values["podcast"] = podcast

        await step_context.context.send_activity(
            MessageFactory.text(f"你的選擇是：{podcast}")
        )

        return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("請輸入你想搜尋的內容，若是輸入關鍵字，請用「，」分隔。")),
        )
    
    async def confirm_step( self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["query"] = step_context.result
        
        user_profile = await self.user_profile_accessor.get(
                step_context.context, UserProfile
        )    
        user_profile.podcast = step_context.values["podcast"]
        user_profile.query = step_context.values["query"]

        processor = TextProcessor()
        user_query = processor.word_segmentation(user_profile.query, True)
        db_query = CosmosDBQuery(connection_string, 'Score','stopwords.txt')
        resulting_terms = db_query.process_query(user_query)
        search_result = (json.dumps(resulting_terms, ensure_ascii=False, indent=4))
        msg = f"節目：{user_profile.podcast} \n搜尋內容：{search_result}"

        await step_context.context.send_activity(MessageFactory.text(msg))

        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("是否滿意此搜尋結果？")),
        )
    
    async def summary_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["satisfied"] = step_context.result
        if step_context.values["satisfied"]:
            return await step_context.prompt(
                ConfirmPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("你想搜尋其他的Podcast節目嗎？")),
            )
        else:
            return await step_context.prompt(
                ConfirmPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("是否要再重新輸入搜尋內容呢？")),
            )
    async def handle_query_again(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if not step_context.values["satisfied"]:
            query_another = step_context.result
            if query_another: #modify -> 回到query_step
                # step_context.context.active_dialog.state["stepIndex"] = step_context.context.active_dialog.state["stepIndex"] - 3
                # return await self.query_step(step_context)
                return await step_context.replace_dialog(self.initial_dialog_id)
            else:         
                return await step_context.prompt(
                ConfirmPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("你想搜尋其他的Podcast節目嗎？")),
                )
        else:
            step_context.values["search_another"] = step_context.result
            return await step_context.continue_dialog()

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.values["satisfied"]:
            search_another = step_context.values["search_another"]
        else: 
            search_another = step_context.result
            
        if search_another:
            return await step_context.replace_dialog(self.initial_dialog_id)
        else:
            await step_context.context.send_activity(MessageFactory.text('搜尋結束，謝謝您~'))
            return await step_context.end_dialog()
