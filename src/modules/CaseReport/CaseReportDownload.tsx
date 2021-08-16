import React, { useEffect, useState } from 'react'
import { getMockCaseReport } from '../../../__mocks__/ScoutResponses'
import { getCaseReport } from 'services/ScoutApi'
import { CaseReportPDF } from '../../components/CaseReport/CaseReportPDF'
import { DownloadOutlined } from '@ant-design/icons'
import { PDFDownloadLink } from '@react-pdf/renderer'

export const CaseReportDownload = () => {
  const [report, setReport] = useState<any>()

  useEffect(() => {
    getCaseReport()
      .then((response: any) => {
        console.log(response)
        setReport(response.report.data.case)
      })
      .catch(() => {
        setReport(getMockCaseReport.data.case)
      })
  }, [])
  return (
    <>
      <DownloadOutlined twoToneColor="#eb2f96" size={900} style={{ fontSize: 20 }} />
        <a href={'./'}>Case report page</a>
      <PDFDownloadLink document={<CaseReportPDF />} fileName="report.pdf">
        {({ blob, url, loading, error }) => (loading ? 'Loading document...' : 'General report')}
      </PDFDownloadLink>
    </>
  )
}
