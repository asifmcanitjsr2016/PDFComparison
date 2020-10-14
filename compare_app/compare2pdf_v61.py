import re
import fitz
import difflib

class ComparePDF:

    def __init__(self, pdf1, pdf2, pdf_output):        
        self.pdf_words_list_1 = []        
        self.pdf_words_list_2 = []
        self.pdf1_words_list = []        
        self.pdf2_words_list = []
        self.pdf1_t_del = []                
        self.pdf2_t_add = []        
        self.pdf1_pages_size = []
        self.pdf2_pages_size = []
        self.json_output = []              
        self.border = 10        
        self.output_pdf = fitz.open()        
        self.pdf1_path = pdf1
        self.pdf2_path = pdf2
        self.pdf1 = fitz.open(self.pdf1_path)
        self.pdf2 = fitz.open(self.pdf2_path)
        self.update_pdf_pages_size()
        self.n1 = self.pdf1.pageCount
        self.n2 = self.pdf2.pageCount
        self.pdf_out = pdf_output
        self.image_border = 3
        self.pdf_words_list_1_count = 0
        self.pdf_words_list_2_count = 0        
        self.parse_words(1)
        self.parse_words(2)

    def update_pdf_pages_size(self):
        n1 = self.pdf1.pageCount
        n2 = self.pdf2.pageCount
        for p in range(n1):
            page_a = self.pdf1[p]
            size = page_a.MediaBox
            self.pdf1_pages_size.append([size[2], size[3]])
        for p in range(n2):
            page_b = self.pdf2[p]
            size = page_b.MediaBox
            self.pdf2_pages_size.append([size[2], size[3]])

    def parse_words(self, pdf, page_start=0, page_end=None):        
        current_pdf = None  
        i = 0

        if pdf == 1:
            current_pdf = self.pdf1
        elif pdf == 2:
            current_pdf = self.pdf2

        if current_pdf is not None:
            page_number = current_pdf.pageCount                        
            start = 0                        
            for p in range(start, page_number):
                for text in current_pdf[p].getText("words"):
                    tmp_list = list(text)                    
                    tmp_list.append(p)                    
                    if pdf == 1:                                                                        
                        self.pdf1_words_list.append(f"{tmp_list[4]}")
                        self.pdf_words_list_1.append(tmp_list)                                                                                               
                    else:                        
                        self.pdf2_words_list.append(f"{tmp_list[4]}")
                        self.pdf_words_list_2.append(tmp_list)                        
                    i += 1
        if pdf == 1:
            self.pdf_words_list_1_count = i            
        else:
            self.pdf_words_list_2_count = i                

    def update_json_text(self, data, type_u):
        type_action = {
            "del": "Delete text",            
            "add": "Add text",
        }        

        p = data[-1]
        x = data[0]
        y = data[1]
        w = data[2]
        h = data[3]
        page_w = 0
        page_h = 0        

        if type_u == "del":
            page_w = self.pdf1_pages_size[p][0]
            page_h = self.pdf1_pages_size[p][1]
        elif type_u == "add":
            page_w = self.pdf2_pages_size[p][0]
            page_h = self.pdf2_pages_size[p][1]        

        template = {            
            "Height": h,
            "Width": w,
            "X": x,
            "Y": y,
            "PageNumber": p,
            "Text": f"{data[4]}",
            "Type": type_action[type_u]
        }
        self.json_output.append(template)
        if type_action[type_u] == 'Delete text':
                self.pdf1_t_del.append(template)
        elif type_action[type_u] == 'Add text':
                self.pdf2_t_add.append(template)                        

    def diff_from_comp(self):        
        totalWord = max(self.pdf_words_list_1_count,self.pdf_words_list_2_count)
        txt = ""
        i = 0
        pdf1_word_pos = 0
        pdf2_word_pos = 0
        for diff in difflib.unified_diff(self.pdf1_words_list, self.pdf2_words_list, n = totalWord):
            if i < 3:
                i += 1
                continue
            if diff.startswith(' '):
                pdf1_word_pos += 1
                pdf2_word_pos += 1

            elif diff.startswith('-'):
                data = self.pdf_words_list_1[pdf1_word_pos]                
                self.update_json_text(data,"del")
                pdf1_word_pos += 1
            elif diff.startswith('+'):
                data = self.pdf_words_list_2[pdf2_word_pos]                
                self.update_json_text(data,"add")
                pdf2_word_pos += 1                        

    #Hightlight changes            
    def diff_text_highlight(self):        
        n1 = self.pdf1.pageCount
        n2 = self.pdf2.pageCount
        n = max(n1, n2)

        for i in range(n):
            page_com = self.output_pdf[i]
            if i < n1:                
                for rect in self.pdf1_t_del:                    
                    if i == rect['PageNumber']:                    
                        gg = fitz.Rect(
                            rect['X'] + self.border, rect['Y'] + self.border, rect['Width'] + self.border, rect['Height'] + self.border)
                        highlight = page_com.addHighlightAnnot(gg)
                        highlight.setColors({"stroke": (1, 0, 0)})
                        highlight.setOpacity(0.75)
                        highlight.update()                
            if i < n2:
                if i < n1:
                    page_tmp = self.pdf1[i]
                else:
                    page_tmp = self.pdf2[i]
                size = page_tmp.MediaBox
                for rect in self.pdf2_t_add:                    
                    if i == rect['PageNumber']:
                        gg = fitz.Rect(rect['X'] + self.border * 2 + size[2], rect['Y'] +
                                            self.border, rect['Width'] + self.border * 2 + size[2], rect['Height'] + self.border)
                        highlight = page_com.addHighlightAnnot(gg)
                        highlight.setColors({"stroke": (0, 1, 0)})
                        highlight.setOpacity(0.75)
                        highlight.update()                

        if self.file_writable(self.pdf_out):
            print("@@@"*20)
            print(self.pdf_out)
            self.output_pdf.save(self.pdf_out)

    def page_add_border(self):
        
        n1 = self.pdf1.pageCount
        n2 = self.pdf2.pageCount
        col = (0, 0, 0)        
        for i in range(n1):
            page_a = self.pdf1[i]
            size = page_a.MediaBox
            page_a.drawRect(fitz.Rect(
                0, 0, size[2], size[3] - 1), color=col, overlay=True, width=1)            
        for i in range(n2):
            page_b = self.pdf2[i]
            size = page_b.MediaBox
            page_b.drawRect(fitz.Rect(
                0, 0, size[2], size[3] - 1), color=col, overlay=True, width=1)            

        for i in range(max(n1, n2)):
            if i < n1 and i < n2:
                page_a = self.pdf1[i]
                page_b = self.pdf2[i]
                size1 = page_a.MediaBox
                size2 = page_b.MediaBox

                page_c = self.output_pdf.newPage(-1, size1[2] + size2[2] + self.border * 3, max(
                    size1[3], size2[3]) + self.border * 2)

                r1 = fitz.Rect(self.border, self.border,
                               size1[2] + self.border, size1[3] + self.border)
                r2 = fitz.Rect(size1[2] + self.border * 2, self.border,
                               size1[2] + size2[2] + self.border * 2, size2[3] + self.border)

                page_c.showPDFpage(r1, self.pdf1, i)
                page_c.showPDFpage(r2, self.pdf2, i)

            elif i < n1:
                page_a = self.pdf1[i]
                size1 = page_a.MediaBox
                page_c = self.output_pdf.newPage(-1, size1[2] + size1[2] + self.border * 3, max(
                    size1[3], size1[3]) + self.border * 2)
                r1 = fitz.Rect(self.border, self.border,
                               size1[2] + self.border, size1[3] + self.border)
                col = (1, 0, 0)
                page_c.drawRect(r1, color=col, overlay=True, width=1)
                page_c.showPDFpage(r1, self.pdf1, i)

            elif i < n2:
                page_b = self.pdf2[i]
                size2 = page_b.MediaBox
                page_c = self.output_pdf.newPage(-1, size2[2] + size2[2] + self.border * 3, max(
                    size2[3], size2[3]) + self.border * 2)
                r2 = fitz.Rect(size2[2] + self.border * 2, self.border,
                               size2[2] + size2[2] + self.border * 2, size2[3] + self.border)
                page_c.showPDFpage(r2, self.pdf2, i)

    def diff_image_highlight(self):
        
        page_number1 = self.pdf1.pageCount
        page_number2 = self.pdf2.pageCount
        images1_base64 = []
        images2_base64 = []

        i = 1
        for p in range(page_number1):
            page = self.pdf1[p]
            html = page.getText("html")
            html = re.sub("\n", "¶", html)
            m = re.findall(
                r"<img.*?top:(\d+)pt;left:(\d+)pt;width:(\d+)pt;height:(\d+)pt.*?base64,\s*(.*?)\">", html, re.M | re.I)
            for data in m:                
                y = int(data[0])
                x = int(data[1])
                w = int(data[2])
                h = int(data[3])
                img_txt = data[4]
                images1_base64.append([x, y, w, h, img_txt, i, p])
                i += 1
        for p in range(page_number2):
            page = self.pdf2[p]
            html = page.getText("html")
            html = re.sub("\n", "¶", html)
            m = re.findall(
                r"<img.*?top:(\d+)pt;left:(\d+)pt;width:(\d+)pt;height:(\d+)pt.*?base64,\s*(.*?)\">", html, re.M | re.I)
            for data in m:                
                y = int(data[0])
                x = int(data[1])
                w = int(data[2])
                h = int(data[3])
                img_txt = data[4]
                images2_base64.append([x, y, w, h, img_txt, i, p])
                i += 1
            
        # Highlight images
        for p in range(page_number1):
            page = self.pdf1[p]
            for dd in images1_base64:
                if dd[-1] == p:
                    col = (1, 0, 0)
                    for tt in images2_base64:
                        if dd[4] == tt[4]:
                            col = (1, 1, 1)
                    page.drawRect(fitz.Rect(dd[0] - 5, dd[1] - 5, dd[0] + dd[2] + 10 - self.image_border,
                                                 dd[1] + dd[3] + 10 - self.image_border), color=col, overlay=True, width=self.image_border)                    

        for p in range(page_number2):
            page = self.pdf2[p]
            for dd in images2_base64:
                if dd[-1] == p:
                    col = (0, 1, 0)
                    for tt in images1_base64:
                        if dd[4] == tt[4]:
                            col = (1, 1, 1)
                    page.drawRect(fitz.Rect(dd[0] - 5, dd[1] - 5, dd[0] + dd[2] + 10 - self.image_border,
                                                 dd[1] + dd[3] + 10 - self.image_border), color=col, overlay=True, width=self.image_border)                        

    @staticmethod
    def file_writable(filepath):
        try:
            open(filepath, 'w')
        except IOError:
            print(f"WARNING: Unable to write in the \"{filepath}\" file")
            return False
        return True
