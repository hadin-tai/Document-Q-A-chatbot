from fastapi.responses import JSONResponse

def success_response(data=None, message="Success", status_code=200):
    content = {
        "success": True,
        "message": message
    }
    if data is not None:
        content.update(data)
    
    return JSONResponse(content=content, status_code=status_code)

def error_response(message="An error occurred", status_code=400):
    return JSONResponse(
        content={
            "success": False,
            "message": message
        },
        status_code=status_code
    )
