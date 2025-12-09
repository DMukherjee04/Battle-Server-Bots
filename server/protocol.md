# Game Protocol :

1. JOIN :

    Client -> Server : 
        {
            "type": "JOIN",
            "id": "<player-id>"
        }
        
    Server -> Client : 
        {
            "type": "WELCOME",
            "id": "<player-id>"
        }
    
2. ATTACK :

    Client -> Server : 
        {
            "type": "ATTACK",
            "id": "<player-id>"
        }
    
    Server -> Client : 
        {
            "type": "ATTACKED",
            "id": "<player-id>"
        }

3. MOVE :

    Client -> Server : 
        {
            "type": "MOVE",
            "id": "<player-id>",
            "x_old" : <int>,
            "y_old" : <int>,
            "dx" : <int> (x_new - x_old),
            "dy" : <int> (y_new - y_old)
        }
    
    Server -> Client : 
        {
            "type": "MOVED",
            "id": "<player-id>",
            "x" : <int> (x_new),
            "y" : <int> (y_new)
        }

4. LEFT :

    Client -> Server : 
        {
            "type": "LEFT",
            "id": "<player-id>",
        }

