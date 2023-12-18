from gamestate import GameState
import tools
import evaluate

import requests
import json
import boto3

def lambda_handler(event, context):
    """AWS Lambda Handler function. 
    This is the entry point defined in AWS Lambda.
    """
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
        
        if game.move < 2:
            depth = 2
        else:
            depth = evaluate.update_depth(game)

        eval, best_move = game.search()

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
        lambda_function_name = ${lambda_arn}

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
        api_url = ${api_gateway_arn}

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

if __name__ == "__main__":
    new_lambda = LambdaUCI()
    new_lambda.lambda_game()
