# simple-jwt-otp-authentication-backend
An JWT based authentication system that uses OTP instead of passwords

# APIs Contracts:

### Authentication (SignUp/SignIn):

Path: /user
UseCase: SignUp & Login
Type: Get
Request:
 
#### (Step 1: Initial request)å
```
{
    "email":"johndoe@email.com",
    "requestType": "LOGIN_OTP_GENERATION"
}
```
>Content to be sent as params.. /user?email=”johndoe@email.com”&requestType=”LOGIN_OTP_GENERATIONS”

##### Success Response:
```
{
    "email" "johndoe@email.com",
    "status": "SUCCESS"
}
```
##### ON FAILURE
(Step 1.5) 
> Status: SUCCESS
        FAILURE
	      BLOCKED

#### (Step-2 Login)
```
{
    "email" "johndoe@email.com",
    "otp": 23345436,
    "requestType": "LOGIN"
}
```

##### SuccessResponse:
```
{
    "email" "johndoe@email.com",
    "status": "SUCCESS"
}
```

>Access and refresh tokens will be sent after LOGIN request.




### NEW_USER REGISTRATION
Type: Post
```
{
    "email" "johndoe@email.com",
    “first_name”: “john”,
    “last_name”: “doe”,
    "requestType": "REGISTER_NEW_USER"
}
```



#### SUCCESS_RESPONSE
```
{
    "email" "johndoe@email.com",
    "status": "SUCCESS"
}
```

> Status: SUCCESS
	:  Failure (On failure => display contact admin)


#### (Step 2: Request with OTP)
```
{
    "email" "johndoe@email.com",
    "otp": 23345436,
    "requestType": "LOGIN"
}
```

#### SuccessResponse:
```
{
    "email" "johndoe@email.com",
    "status": "SUCCESS"
}
```

>Access and refresh tokens will be sent after LOGIN request.


#### FailureResponse:
````
{
    "email" "johndoe@email.com",
    "userId": "id",
    "status": "USER_BLOCKED"
}
````

>Response Status Enums:
* USER_BLOCKED
* INVALID_OTP
* ATTEMPTS_EXCEEDED
* USER_DOESNOT_EXIST
* SUCCESS

### Logout 

Path: /user
UseCase: Logout
Type: Post
Request: 
```
{
    "requestType": "LOGOUT",
    “loginId”:[7,3,4] or 7 //optional for selected logouts.
    “userId”:aad-433-vvf //optional
}
```


> * If id is not provided, only that device is logged out.
* If userid is provided, all logins of user is logged out.
* Priority:
* loginId-->userid



GET /user
/user?requestType=”LOGGED_DEVICES”
```
[
    {
        "id": 22,
        "last_login": "2021-08-06T11:51:24.635431",
        "auto_logout": "2022-08-06T11:51:24.635431",
        "device": "PostmanRuntime/7.28.2",
        "os": "",
        "location": ""
    },
    {
        "id": 23,
        "last_login": "2021-08-06T12:18:14.220304",
        "auto_logout": "2022-08-06T12:18:14.220304",
        "device": "PostmanRuntime/7.28.2",
        "os": "",
        "location": ""
    }
]
```



### Refresh:
Path: /refresh
Type: Get
Request:
```
{
    "oldRefrestToken": "token1",
    "expiryDate": "timestamp"
}
```


### UserInformation:
Path: /user/profile
Type: Get
Request:
```
{
    "email": "johndoe@email.com",
    "InformationList": [
        Address,
        PhoneNumber,
        Email,
     ]
}
```

#### Response:
```
{
    "email": "johndoe@email.com",
    "status": "SUCCESSFUL"
    "Information": {
        "Address": "address 1",
        "PhoneNumber": "947569846",
        "Email": "johndoe@email.com"
    }
}
```

auth/request-validation/

Proxy Request Object to this URL. 
Response:
```
{
    "email" "johndoe@email.com",
    "id": aa53-bh11-ii43-pp11,
    "status": "SUCCESS",
    “first_name”: “john”,
    “last_name”:”doe”
}
```



For failure
```
{
    "status": "FAILURE",
    “detail”:”USER_NOT_AUTHENTICATED”   
}
```