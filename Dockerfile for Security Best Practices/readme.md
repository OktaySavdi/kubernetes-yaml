
### Check the securi-api Dockerfile

1.  Check the  `securi-api`  Dockerfile:
    
    ```
    vi securi-api
    ```
    
2.  Delete the first line  `RUN apt-get update && apt-get install -y mathblasters`.
    
3.  To save and exit the file, press  **Escape**, type  `:wq`, and hit  **Enter**.

### Check the securi-webserver Dockerfile

1.  Check the  `securi-webserver`  Dockerfile:
    
    ```
    vi securi-webserver
    ```
    
2.  On the final  `USER`  directive, replace the  `root`  user with  `nginxuser`.
    
3.  To save and exit the file, press  **Escape**, type  `:wq`, and hit  **Enter**.

### Check the securi-users Dockerfile

1.  Check the  `securi-users`  Dockerfile:
    
    ```
    vi securi-users
    ```
    
2.  Delete the line  `ENV db_password=hunter2`  to remove the password from the image.
    
3.  To save and exit the file, press  **Escape**, type  `:wq`, and hit  **Enter**.
