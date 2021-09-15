import React from 'react'
import { CaseReportPDF } from '../../components/CaseReport/CaseReportPDF'
import { DownloadOutlined } from '@ant-design/icons'
import { PDFDownloadLink } from '@react-pdf/renderer'

export const CaseReportDownload = () => {
	return (
		<>
			<PDFDownloadLink document={<CaseReportPDF />} fileName="report.pdf">
				{({ blob, url, loading, error }) =>
					loading ? (
						'Loading document...'
					) : (
						<DownloadOutlined twoToneColor="#eb2f96" size={900} style={{ fontSize: 20 }} />
					)
				}
			</PDFDownloadLink>
		</>
	)
}
