import React from 'react'
import styles from './CasePage.module.css'
import { DownloadOutlined } from '@ant-design/icons'
import { Card } from 'antd'

export const CasePage = () => {
  return (
    <div className={styles.container}>
      <Card style={{ width: 130 }}>
        <DownloadOutlined twoToneColor="#eb2f96" size={900} style={{ fontSize: 60 }} />
        <div>Case report</div>
      </Card>
    </div>
  )
}
