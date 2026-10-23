from rest_framework.response import Response

def success_response(
        data = None,
        messgae = "Success",
        status_code = 200
):
    return Response(
        {
            "success": True,
            "messgae": message,
            "data": data
        },
        Status = status_code
    )