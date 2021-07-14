import React, { useState } from 'react'
import Typography from '@material-ui/core/Typography'
import styles from './CasesTable.module.css'

export const CasesTable = () => {
  const [cases, setCases] = useState()
  return (
    <Typography variant="body1" component="p" className={styles.body}>
      Scout allows you to browse VCFs in a web browser, identify compound pairs, and solve cases as
      a team.
    </Typography>
  )
}
