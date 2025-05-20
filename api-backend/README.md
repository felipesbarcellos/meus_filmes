# MeusFilmes API Backend

## 🎬 Project Overview

This project is a RESTful API built with Flask, serving as the backend for the MeusFilmes platform. It uses a modular architecture with Blueprints to organize routes and provides endpoints for managing users, movie lists, watched movies, and interacting with the TMDB (The Movie Database) API. Interactive API documentation is available via Swagger UI.

## ✨ Main Features

*   **User Authentication:** Registration, login, and (to be implemented) password recovery using JWT tokens.
*   **Movie List Management:** Create, view, update, and delete custom movie lists.
*   **Watched Movies Tracking:** Users can record movies they've watched, including the date.
*   **TMDB Integration:** Proxy for popular TMDB endpoints such as movie search, details, genres, and recommendations.
*   **Modular Structure:** Code organized using Flask Blueprints to separate concerns (authentication, lists, etc.).
*   **API Documentation:** OpenAPI specification (`openapi.yaml`) served and viewable via Swagger UI at `/api/docs`.

## 🚀 Getting Started

Instructions for starting the frontend are included in the main project README. See the [main README](../README.md) for instructions on how to set up and run the entire MeusFilmes project.

### Running the Backend Application
Details on how to run the backend (usually via Docker Compose) are described in the root README.

For exact request/response schema details, see the `openapi.yaml` specification or the Swagger UI interface at `/api/docs`.

## 🛠️ Tech Stack
*   Flask
*   Flask-SQLAlchemy
*   Flask-Cors
*   Flask-Swagger-UI
*   SQLAlchemy
*   Docker
*   Docker Compose
*   Python