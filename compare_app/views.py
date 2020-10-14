from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .compare2pdf_v61 import ComparePDF
from rest_framework.renderers import TemplateHTMLRenderer
from django.conf import settings
import logging
class FileView(APIView):
    
    def post(self, request, *args, **kwargs):
        log = logging.getLogger(__name__)        
        try:            
            log.info("Test log in django!")
            uploaded = request.data        
            pdf_old = f'{uploaded["pdf_old"]}'.strip("/")
            pdf_new = f'{uploaded["pdf_new"]}'.strip("/")
            output_pdf = f'{uploaded["pdf_output"]}'.strip("/")
            output_file = output_pdf
            source = f'{uploaded["source"]}'.strip("/")
            print(uploaded)
            if source == "Web":
                pdf_old = settings.INPUT_FILE_PATH + pdf_old
                pdf_new = settings.INPUT_FILE_PATH + pdf_new
                output_pdf = settings.OUTPUT_FILE_PATH + output_pdf
                # if os.path.exists(output_pdf):
                #     return Response(output_file)

            C1 = ComparePDF(pdf_old, pdf_new, output_pdf)            
            C1.diff_from_comp()
            if source == "Web":
                C1.diff_image_highlight()
                C1.page_add_border()
                C1.diff_text_highlight()
                self.releaseResource(C1)
                return Response(output_file)            
            else:
                self.releaseResource(C1)
                return Response(C1.json_output)                         
        except Exception as e:
            log.error(e)
    def releaseResource(self, pdfObject):
        pdfObject.output_pdf.close()
        pdfObject.pdf1.close()
        pdfObject.pdf2.close()

def homepage(request):
    log = logging.getLogger(__name__)
    log.info("loading homepage")
    return render(request, 'index.html')