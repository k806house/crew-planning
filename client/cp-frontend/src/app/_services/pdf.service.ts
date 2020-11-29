import {Injectable} from '@angular/core';
import pdfMake from 'pdfmake/build/pdfmake';
import pdfFonts from 'pdfmake/build/vfs_fonts';

pdfMake.vfs = pdfFonts.pdfMake.vfs;

@Injectable({
  providedIn: 'root'
})
export class PdfService {

  constructor() {
  }

  generatePdf() {
    const documentDefinition = {content: 'This is an sample PDF printed with pdfMake'};
    pdfMake.createPdf(documentDefinition).open();
  }

  getDocumentDefinition() {
    sessionStorage.setItem('resume', JSON.stringify(this.resume));
    return {
      content: [
        {
          text: 'RESUME',
          bold: true,
          fontSize: 20,
          alignment: 'center',
          margin: [0, 0, 0, 20]
        },
        {
          columns: [
            [{
              text: this.resume.name,
              style: 'name'
            },
              {
                text: this.resume.address
              },
              {
                text: 'Email : ' + this.resume.email,
              },
              {
                text: 'Contant No : ' + this.resume.contactNo,
              },
              {
                text: 'GitHub: ' + this.resume.socialProfile,
                link: this.resume.socialProfile,
                color: 'blue',
              }
            ],
            [
              this.getProfilePicObject()
            ]
          ]
        }],
      styles: {
        name: {
          fontSize: 16,
          bold: true
        }
      }
    };
  }

}
