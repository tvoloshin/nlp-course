import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from classification_service.nlp_models.stub_model import StubModel

model = StubModel()


@require_POST
@csrf_exempt
def classify(request):
    data = json.loads(request.body)

    result = model.predict(data.get("text"))

    response = {
        "label": result[0],
        "certainty": result[1]
    }

    return JsonResponse(response)
