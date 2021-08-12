import React, { useEffect, useState } from 'react'
import { getMockCaseReport } from '../../../__mocks__/ScoutResponses'
import styles from './CaseReport.module.css'
import { getCaseReport } from 'services/ScoutApi'
import { DownloadOutlined } from '@ant-design/icons'

export const CaseReportPage = () => {
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
  return report ? (
    <div className={styles.container}>
      <DownloadOutlined twoToneColor="#eb2f96" size={900} style={{ fontSize: 60 }} />
      {report.display_name}
    </div>
  ) : (
    <div>Loading</div>
  )
}
