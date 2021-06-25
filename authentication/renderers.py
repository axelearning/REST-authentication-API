from rest_framework import  renderers
import json

class UserRenderer(renderers.JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type, renderer_context):
        if 'ErrorDetail' in str(data):
            errors = {}
            for key, value in data.items():
                errors[key] = value[0] if isinstance(value, list) else value
            return json.dumps({'errors': errors})
        else:
            return super().render({'success': data})