from gamestate import GameState
import tools
import evaluate
import gc

import requests
import json
import boto3

def lambda_handler(event, context):
    """AWS Lambda Handler function. This is the entry point defined in AWS Lambda."""
    request_body = event.get('moves')

    new_lambda = LambdaUCI()
    best_move = new_lambda.lambda_helper(request_body)

    headers = {
            "Content-Type": "application/json"
        }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'best_move': str(best_move)
        }

class LambdaUCI:
    def __init__(self) -> None:
        self.eval_func = evaluate.evaluate_board
        self.depth = 4

    # UCI interface
    def lambda_game(self):
        gc.disable()
        while(True):
            command = input()
            parsed_command = command.split(" ")

            if parsed_command[0] == "uci":
                print("id name Dex 0.0")
                print("id author Edward Kong")
                print("uciok")

            elif parsed_command[0] == "isready":
                print("readyok")

            elif parsed_command[0] == "position":
                self.stored_position = parsed_command

            elif parsed_command[0] == "go":
                request_body = self.generate_request(self.stored_position, parsed_command)
                response = self.invoke_lambda(request_body)
                self.make_move(response)

            elif parsed_command[0] == "stop":
                quit()

            elif parsed_command[0] == "quit":
                quit()

    def lambda_helper(self, moves=None):
        if moves is None:
            moves = []

        else:
            moves = moves

        game = GameState()
        game.newGameUCI()

        for move in moves:
            given_move = tools.uci_to_int(move, game.board.bitboards)
            game.make_move(given_move)
        
        if game.move < 3:
            depth = 2
        if game.move > 20:
            depth = evaluate.update_depth(game)
        
        else:
            depth = self.depth

        eval, best_move = game.search(depth, game.turn, evaluate.evaluate_board)

        return best_move
    
    def generate_request(self, position, go=None):
        """Prepares payload."""
        moves = []
        if len(position) > 2:
            if position[2] == "moves":
                moves = position[3:]
        
        body = {
            "moves": moves
        }
        return body
    
    def invoke_lambda(self, payload):
        """Invokes lambda function."""
        lambda_function_name = 'arn:aws:lambda:us-east-2:942356009231:function:dex'

        # Create a Boto3 Lambda client
        lambda_client = boto3.client('lambda')

        # Invoke the Lambda function
        response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload),
        )

        return response

    def send_request(self, payload):
        """Sends request to API Gateway."""
        api_url = "https://a38t8757nf.execute-api.us-east-2.amazonaws.com/Dev/find-move"

        headers = {
            "Content-Type": "application/json"
        }

        # Make the POST request
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)

        #print(response.status_code)
        return response
    
    def make_move(self, response):
        """Reads response and sends to UCI GUI."""
        boto_response = json.loads(response.get('Payload').read().decode('utf-8'))
        if boto_response.get('statusCode') == 200:
            best_move = tools.int_to_uci(int(boto_response.get('best_move')))
            print(f"bestmove {best_move}")
        else:
            # If the request was not successful, print an error message
            print(f"Error: {boto_response.get('statusCode')}")
        return None

"""Response Format
{'ResponseMetadata': {
    'RequestId': '37ccb4a9-93ea-4de1-a32d-10cb0e2c49b9', 
    'HTTPStatusCode': 200, 
    'HTTPHeaders': {
        'date': 'Wed, 06 Dec 2023 23:05:58 GMT', 
        'content-type': 'application/json', 
        'content-length': '89', 
        'connection': 'keep-alive', 
        'x-amzn-requestid': '37ccb4a9-93ea-4de1-a32d-10cb0e2c49b9', 
        'x-amzn-remapped-content-length': '0', 
        'x-amz-executed-version': '$LATEST', 
        'x-amzn-trace-id': 'root=1-6570fe56-4dd9da7033705f415eade5b3;sampled=0;lineage=b1aeed8b:0'
        }, 
   'RetryAttempts': 0
   }, 
   'StatusCode': 200, 
   'ExecutedVersion': '$LATEST', 
   'Payload': <botocore.response.StreamingBody object at 0x7fd2300fea90>
   }
"""

if __name__ == "__main__":
    new_lambda = LambdaUCI()
    new_lambda.lambda_game()