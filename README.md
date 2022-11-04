# Climate-Data-Daily-IDN

In this project I use [Climate Data Daily IDN](https://www.kaggle.com/datasets/greegtitan/indonesia-climate)
dataset to demonstrate and compare the performance of various forecasting models.

## Startup

To start the application:
1. Create Python environment `python3 -m venv venv`
2. Activate the environment `source venv/bin/activate`
3. Install required packages `pip install -r requirements.txt`
4. Start the streamlit app `./streamlit.sh`

    
## Deploy with Docker

To run the streamlit application as a docker container

    
    docker compose up --build -d


## Deploy with Heroku


1. Install heroku cli - [doc](https://devcenter.heroku.com/articles/heroku-cli)
2. Log in to Heroku `heroku login`
3. Create the app `heroku create climate-data-indonesia`
4. Add git remote `heroku git:remote -a climate-data-indonesia`
5. Commit code and deploy it to Heroku
 

    git add .
    git commit -am "adding streamlit app"
    git push heroku main`
