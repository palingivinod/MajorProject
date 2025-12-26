# from executor import gmail_sender as gs

# # 1. body but no subject
# #print(gs.send_email({"to":"vinod","body":"Hi Prasanth, let's sync tomorrow about the release."}))

# # 2. explicit subject
# #print(gs.send_email({"to":"vinod","subject":"Status update","body":"All tests passed."}))
# print(gs.send_email({
#     "to": "prasanth",
    
#     "body": "Hi , Sanka go and beg ."
# }))

import dateparser

dateparser.parse("next friday at 3pm")