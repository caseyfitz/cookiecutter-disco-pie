# Cookiecutter DiscoPie: Deployment Inside Serverless Containers of Python-Integrated Endpoints
***Dread deploying your API? Use Cookiecutter DiscoPie!***
___

## Do I want Cookiecutter DiscoPie?

Ever built a *sik* ML model only to find that it's *stuck* on your stupid laptop, beefy desktop, or ephemeral cloud machine? Do you *need* the world to have access to ur dope deep learning model? Do you *loathe* the idea of navigating the [treacherous waters](https://twitter.com/iamdevloper/status/912185400336232449) of the AWS UI? Do you *insist* on containerizing your code because I mean what else are you doing is this 2015 or something? Do you *require* serverless deployment because what is a server?

If you answered "yes" to *every single one* of the above questions, then you've come to right place. Cookiecutter DiscoPie is here to handle all the annoying stuff so you can focus on serving that model, or whatever else people do with REST APIs.

Cookiecutter DiscoPie
1. *Templatizes* a an API endpoint based on [FastAPI](https://fastapi.tiangolo.com). You just need to import the code.
2. *Containerizes* the service and provides commands for local interaction.
3. *Deploys* the container as a serverless REST endpoint (currently only on AWS, but we have a vision).

## Do I *need* Cookiecutter DiscoPie?

Probably not. There are other ways to do this. But they either [don't support containers](https://github.com/aws/chalice), or [require](https://aws.amazon.com/blogs/machine-learning/using-container-images-to-run-pytorch-models-in-aws-lambda/) silly command line steps. You are a *Python* [data scientist](https://www.hbs.edu/faculty/Pages/item.aspx?num=43110), dammit, not  [Kevin Mitnick](https://en.wikipedia.org/wiki/Kevin_Mitnick)!

Plus, our FastAPI-based design means there's hope for supporting multiple serverless cloud backends (huge caveat: there needs to exist an ASGI [adapter](https://github.com/jordaneremieff/mangum) for each).

Just try it, you nerd!

## To create a new API, run:
```
cc-disco-pie https://www.github.com/caseyfitz/cookiecutter-disco-pie
```
