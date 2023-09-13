from typing import  Dict, List

from presidio_analyzer.recognizer_result import RecognizerResult

class AnalyzerResponse:
    def __init__(self, id, result: List[RecognizerResult], error=''):
        self.id = id
        self.result = result
        self.error = error

    def to_dict(self) -> Dict:
        """
        Serialize self to dictionary.

        :return: a dictionary
        """
        return self.__dict__