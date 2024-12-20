# deployment updates

## Goals
We have built the backend and are now working on the frontend. The backend has been tested and all the endpoints are working. We are now working on the frontend and will be deploying the frontend and backend together.

## Current Status
the database for backend is using postgres.
```bash
psql -U giraffe -d typeracer_db
```

## API Endpoints Reference

| **Endpoint**        | **Method** | **Description**                                   | **Status**    |
|---------------------|------------|--------------------------------------------------|---------------|
| `/connect_user`     | POST       | Connects a user and fetches TypeRacer data       | ✅ Working    |
| `/fetch_data`       | POST       | Fetch race data for a user                       | ✅ Working    |
| `/load_data`        | GET        | Load data from PostgreSQL database               | ✅ Working    |
| `/generate_code`    | POST       | Generate Python code for queries                 | ✅ Working    |
| `/execute_code`     | POST       | Execute the generated code securely              | ✅ Working    |
| `/query_guidance`   | GET        | Return suggested analysis questions              | ✅ Working    |
| `/player_dashboard` | GET        | Retrieve player statistics and dashboard         | 🚧 To Do      |

## Frontend
run `npx shadcn@latest add "https://v0.dev/chat/b/b_J1Rp8kTy7uF?token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..KbDtryIvUD2O0CTG.aANz12l8NvFRwawQHkn12bKis3_NQCT2i-t2cZSac0wDk2Evm68zdMSQaBM.Ln-p1cpiGjUGRwlWuHNEXQ"` to add the chat component to the frontend.

the frontend is using shadcn/ui.

## Project Structure
├── README.md
├── backend
│   ├── __pycache__
│   ├── app
│   ├── requirements.txt
│   ├── testing_api.py
│   └── venv
├── frontend
│   ├── app
│   ├── components
│   ├── lib
│   ├── pages
│   ├── public
│   ├── styles
│   └── types

## Tasks (one function at a time)
1. Connect user to backend (P0)
2. Fetch data from backend (P0)
3. Generate code from backend (P1)
4. Execute code from backend (P1)
5. Query guidance from backend (P2)
6. Player dashboard from backend (P2)

