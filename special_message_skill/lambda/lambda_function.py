# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.api_client import DefaultApiClient

from ask_sdk_model.services.directive import send_directive_request
from ask_sdk_model.interfaces.tasks.complete_task_directive import CompleteTaskDirective
from ask_sdk_model.interfaces.audioplayer.play_directive import PlayDirective
from ask_sdk_model.interfaces.audioplayer.audio_item import AudioItem
from ask_sdk_model.interfaces.audioplayer.stream import Stream
from ask_sdk_model.interfaces.audioplayer.play_behavior import PlayBehavior

from ask_sdk_core.skill_builder import SkillBuilder, CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to the special message alarm skill! Say help for more info."

        audio_url = "https://johnzhoudev-test-bucket-1.s3.us-east-2.amazonaws.com/clip.mp3?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEJ3%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMiJHMEUCIDwaI%2BNYDVp4DNBseq%2FFotDP%2FPpJQ0InlultFL9zLGQrAiEApRbf7rkMVM08brT3HN%2Bn%2B5UOZy%2F7sNzFkFCfQowY%2Fjkq5AIIFhAAGgwxNzAyMjE2MDgzMzkiDBKZnrOu7Rj6TiyKYSrBAjHJdwIVU7HmfnDh8hjdvM3FJmfw5O4sXJJcMrwQrUdG2IDuuQxmuY8kJ6jo%2FfMDfiESzmtOENuik2QiiE4%2FpNGDJGoSpUk%2BUp0446TOZYMzEMdOGFdSCE%2BqqhFxvAvqkmMCRh1KI7Wkn56YTdHor%2BK5z6Co%2Fk2bzXYaxLJGSOxasTGtbqaXAU9O5sVnsn%2BNXIvPwhGUNeCS0QUxlK50gjstmgC37oBJm9f8H735Rhzv9rtHPU%2FFxTvG6re97ySAnxWaweRT62LEVXQFx22vwFbIOQrWdrTp89QxzksZTK2GxhcfMbPBwf9gA3pHc%2F2SqvOW9gxh7YPRtc93rxcoi6IOjcR0huzKFXLKRBKhrdVHigl%2Fb8h0mFpVA9V3KJbFwWBpSkpD3I7xYxjaUvISLqEl6Sjo4FTVvPPlKgRpFTxGAzD2l9yrBjqzAr7hcIbxE5vsprSUxX73%2F1z1TQgLmFpvCbxqMwH8s60C7AUx%2F6OwYs5LDuKyje8lXXgP6VVlij3TtbaHmdJOeD4ZaKXMGfXm6cJnqqwMA%2BRG6dFe3YJ94QaQtZQMnFNXlyUKQDDLpFcac5Gb%2BDaotGcSIdaF9Ntw3QrMPE3KSlr1v5sQDLcM%2FE8dxOe38XASOqOMmnZjUbK0WrbnW88G1wHJEXrkdU1vBRhAvZSw43tfssue%2BKkL%2B5Pdp%2BEPoqgyNd6367%2BMbrcxiAtqwSr1wh2glf9fss%2BN0gNACuhMphdvHHZTUM5IF6NiFfeOgFxq28ltUwRKKMnqrw1bWGNX0elZwaiQNpNf6ZbwnX2shAiIhwfN0nAdbCk6h7awpgK%2FKqAahVOrbyc34dfkJQux75WwrzQ%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20231211T140017Z&X-Amz-SignedHeaders=host&X-Amz-Expires=900&X-Amz-Credential=ASIASPIP7TWJ46V7PNGR%2F20231211%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Signature=1ec7c4e4b8e0f35513a248ea3c0ccc3d94bf36e243ec701c8b95aec6c7652d58"
        audio_token = "johnzhoudev-test-bucket-1.s3.us-east-2.amasonaws.com/clip.mp3"

        audio_item = AudioItem(
            stream=Stream(
                url=audio_url,
                token=audio_token,
                offset_in_milliseconds=0
            )
        )

        play_directive = PlayDirective(
            play_behavior=PlayBehavior.REPLACE_ALL,
            audio_item=audio_item
        )

        return (
            handler_input.response_builder
                .add_directive(play_directive)
                # .speak(speak_output)
                # .ask(speak_output)
                .response
        )

class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "I'm sorry I'm such a fuking piece of shhhit"

        print(handler_input.response_builder.speak(speak_output).response)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = """To play a special message alarm, the special message should play when you 
          say the open command open special message alarm. Use a routine to invoke this skill and set the routine at a 
          specific time to make it play.
        """

        ask_output = "Is there anything else I can help with? You can say help again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(api_client=DefaultApiClient())

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()