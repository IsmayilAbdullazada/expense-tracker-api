# Expense Tracker API

## Objective

Develop a minimal web API that allows users to manage expense records. This stage is designed to evaluate your ability to quickly design and implement a basic RESTful API.

## Requirements

### 1. Project Setup

*   Create a new web API project using your preferred language and framework (e.g., Node.js/Express, Python/Flask, Java/Spring Boot).

### 2. Expense Data Model

Each expense record must have the following fields:

*   **id:** A unique identifier (auto-generated).
*   **amount:** A numeric value representing the expense amount.
*   **description:** A brief text description of the expense.
*   **date:** The date when the expense was incurred (use a suitable format such as ISO 8601).  Examples: `2024-07-27T14:30:00Z`, `2024-07-27T14:30:00+00:00`, `2024-07-27`.
*   **category:** A string categorizing the expense (e.g., "food", "transport", etc.).

### 3. Endpoints

The API should expose the following endpoints:

| Method | Endpoint           | Description                                      | Request Body                                  | Success Response Code | Error Response Codes                 |
| ------ | ------------------ | ------------------------------------------------ | --------------------------------------------- | --------------------- | ------------------------------------ |
| POST   | `/expenses`        | Create a new expense record.                     | JSON object with `amount`, `description`, `date`, and `category` fields. | 201 Created           | 400 Bad Request (missing/invalid data) |
| GET    | `/expenses`        | Retrieve a list of all expense records.          | None                                          | 200 OK                |                                      |
| GET    | `/expenses/{id}`   | Retrieve a specific expense record by its ID.   | None                                          | 200 OK                | 404 Not Found                        |
| PUT    | `/expenses/{id}`   | Update an existing expense record by its ID.     | JSON object with fields to update.             | 200 OK                | 400 Bad Request, 404 Not Found       |
| DELETE | `/expenses/{id}`   | Delete an expense record by its ID.             | None                                          | 204 No Content        | 404 Not Found                        |

**Example JSON Payload (for POST /expenses):**

```json
{
    "amount": 25.99,
    "description": "Lunch with colleagues",
    "date": "2024-07-27T14:30:00Z",
    "category": "food"
}
