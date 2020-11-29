import {Injectable} from '@angular/core';
import pdfMake from 'pdfmake/build/pdfmake';
import pdfFonts from 'pdfmake/build/vfs_fonts';
import {ScheduleItem} from '../_models';
import {DatePipe} from '@angular/common';
import {newArray} from '@angular/compiler/src/util';

pdfMake.vfs = pdfFonts.pdfMake.vfs;

@Injectable({
  providedIn: 'root'
})
export class PdfService {

  constructor(private datepipe: DatePipe) {
  }

  generatePdf(items: ScheduleItem[]) {

    pdfMake.createPdf(this.getDocumentDefinition(items)).open();
  }

  getDocumentDefinition(items: ScheduleItem[]) {
    const body1 = [['Поезд (туда)', 'Дата отправления (туда)', 'Дата прибытия (туда)', 'Поезд (обратно)', 'Дата отправления (обратно)', 'Дата прибытия (обратно)']];
    console.log(body1);
    for (let item of items) {
      const list: string[] = [item.train_to_title, item.date_start_to.toString(),
        item.date_end_to.toString(), item.train_from_title, item.date_start_from.toString(),
        item.date_end_from.toString()];
      body1.push(list);
    }
    console.log(body1);
    return {
      content: [
        {
          layout: 'lightHorizontalLines',
          table: {
            // headers are automatically repeated if the table spans over multiple pages
            // you can declare how many rows should be treated as headers
            headerRows: 1,
            widths: ['*', 'auto', 100, '*'],

            body: [body1]
          }
        }
      ]
    };
  }

}
