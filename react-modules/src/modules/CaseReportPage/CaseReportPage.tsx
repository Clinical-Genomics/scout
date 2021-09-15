import React from 'react'
import { CaseReportPDF } from '../../components/CaseReport/CaseReportPDF'
import { PDFViewer } from '@react-pdf/renderer'

export const CaseReportPage = () => (
  <PDFViewer width={'100%'} height={'800px'}>
    <CaseReportPDF />
  </PDFViewer>
)
