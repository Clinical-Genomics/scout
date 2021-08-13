import React, { useEffect, useState } from 'react'
import { getMockCaseReport } from '../../../__mocks__/ScoutResponses'
import { getCaseReport } from 'services/ScoutApi'
import { Page, Text, View, Document, StyleSheet } from '@react-pdf/renderer'

const styles = StyleSheet.create({
  page: {
    flexDirection: 'row',
    backgroundColor: '#E4E4E4',
  },
  section: {
    margin: 10,
    padding: 10,
    flexGrow: 1,
  },
})

export const CaseReportPDF = () => {
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
    <Document>
      <Page size="A4" style={styles.page}>
        <View style={styles.section}>
          <Text>Case name: {report.display_name}</Text>
        </View>
        <View style={styles.section}>
          <Text>Owner: {report.owner}</Text>
        </View>
      </Page>
    </Document>
  ) : (
    <Document>
      <Page size="A4" style={styles.page}>
        <View style={styles.section}>
          <Text>Scout React PDF</Text>
        </View>
        <View style={styles.section}>
          <Text>Hej :D</Text>
        </View>
      </Page>
    </Document>
  )
}
