
## Resources & REST API table
| URL/ENDPOINT                            | VERB   | DESCRIPTION                                                        |
| --------------------------------------- | ------ | -----------------------------------------                          |
| /login                                  | POST   | Logs user in { username, password } and returns mongo_id           |
| /signup                                 | POST   | Creates user { username, password } and returns mongo_id           |
| /uploadFormData/                        | POST   | Updates form for matching { fq1, fq2, fq3, fq4, fq5, mongo_id }    |
| /updateBio/                             | POST   | Updates user bio { description, blurb1, blurb2, blurb3, mongo_id } |
||
| /getFriends/                            | POST   | Returns old matches { mongo_id }                         |
| /getBio/                                | POST   | Returns bio { mongo_id }                                 |
| /getFormData/                           | POST   | Returns formData { mongo_id }                            |
| /getUserInfo/                           | POST   | Returns all of the above { mongo_id }                    |
||
| /users/{user_id}/chats                | GET | Gets user contacts and previous messages |
| /users/{user_id}/chats/{chat_user_id} | GET | Gets user chat with specific contact     |

Add friendcode for users in mongodb

\*Sending and receiving new chats will be done through [Flask-Socket](https://github.com/miguelgrinberg/Flask-SocketIO)
ws://{URL}/websockets

