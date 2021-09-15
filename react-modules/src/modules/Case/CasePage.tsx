import React from 'react'
import styles from './CasePage.module.css'
import { Card } from 'antd'
import { CaseReportDownload } from '../CaseReport/CaseReportDownload'

export const CasePage = () => {
	return (
		<div className={styles.container}>
			<Card style={{ width: 130 }}>
				<a href={`${window.location.href}/case_report`}>Case report page</a>
				{'  '}
				<CaseReportDownload />
			</Card>
		</div>
	)
}
