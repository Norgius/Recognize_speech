import json
import argparse

from environs import Env
from google.cloud import dialogflow


def create_intent(
        project_id: str,
        display_name: str,
        training_phrases_parts: list,
        message_texts: list
        ) -> None:
    """Create an intent of the given intent type."""
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)

    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(
            text=training_phrases_part
        )
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )
    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )
    print("Intent created: {}".format(response))


def main():
    env = Env()
    env.read_env()
    project_id = env.str('PROJECT_ID')
    parser = argparse.ArgumentParser(
        description='''Обучает dialogflow фразам, которые \
                       записаны в json-файле'''
    )
    parser.add_argument('-f', default='questions.json',
                        help='укажите путь к json-файлу')
    args = parser.parse_args()

    with open(args.f, 'r') as file:
        training_phrases = json.loads(file.read())
    for intent_name, phrases in training_phrases.items():
        questions = phrases.get('questions')
        answer = [phrases.get('answer')]
        create_intent(project_id, intent_name, questions, answer)


if __name__ == '__main__':
    main()
