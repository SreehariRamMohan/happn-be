
## Resources & REST API table
| URL/ENDPOINT                            | VERB   | DESCRIPTION                               |
| --------------------------------------- | ------ | ----------------------------------------- |
| /login                                  | POST   | Logs user in                              |
| /accountSignup                          | POST   | Creates user { username, password }       |
| /uploadFormData/                        | POST   | Updates form for matching { formData }    |
| /updateBio/                             | POST   | Updates user bio { bioText }              |
| /users/{user_id}/chats                  | GET    | Gets user contacts and previous messages  |
| /users/{user_id}/chats/{chat_user_id}   | GET    | Gets user chat with specific contact      |

\*Sending and receiving new chats will be done through [Flask-Socket](https://github.com/miguelgrinberg/Flask-SocketIO)

