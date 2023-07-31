import requests
import openai
import backoff


class Models:
    SYS_MSG = "You are a helpful assistant who can scrape HTML for relevant information. " \
              "When I give you a piece of HTML, you will extract anything that looks like " \
              "an full name, email, phone number(optional) and department and place them into a list separated by commas."

    def __init__(self, api_text_file):
        """
        Class initializer.

        :param api_text_file: File containing mapping: platform --> api key (text file).
        """
        self.api_text_file = api_text_file
        self.api_keys = {}
        self.__get_api_keys()

    def __get_api_keys(self):
        """
        Read all the api_keys stored in a text file and write them to a dictionary.
        Make sure you store api keys in a text file.
        """
        with open(self.api_text_file, encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                platform, api_key = line.strip().split()
                self.api_keys[platform] = api_key

        openai.api_key = self.api_keys.get(
            'openai', None)  # Initialize openai api

    @backoff.on_exception(backoff.expo, openai.error.RateLimitError)
    def gpt(self, model_name, user_input):
        """
        Query the OpenAI GPT-3 API.

        :param model_name: String denoting what model to deploy.
        :param user_input: Text input you want the model to respond to.
        :return: Generated response from the GPT-3 model.
        """
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": Models.SYS_MSG},
                {"role": "user", "content": user_input},
            ],
            temperature=0,  # Use low temperature for deterministic output
        )
        return response['choices'][0]['message']['content']


if __name__ == "__main__":
    # Create an instance of the Models class with the API text file containing keys.
    models = Models('api_keys.txt')

    # Example usage of GPT-3 endpoint
    user_input = "Some HTML content goes here..."
    response = models.gpt("gpt-3.5-turbo", user_input)
    print("GPT-3 Response:", response)
