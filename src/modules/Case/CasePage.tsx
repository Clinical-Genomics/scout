import React from 'react'
import styles from './CasePage.module.css'
import { Card } from 'antd'

export const CasePage = () => {
  return (
    <div className={styles.container}>
      <Card style={{ width: 130 }}>
        <a href={`${window.location.href}/case_report`}>Case report</a>
      </Card>
    </div>
  )
}
