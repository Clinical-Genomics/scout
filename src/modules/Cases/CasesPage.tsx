import React, { useEffect, useState } from 'react'
import { CasesTable } from 'components/CasesTable/CasesTable'
import styles from './CasesPage.module.css'
import { getCases } from 'services/ScoutApi'

export const CasesPage = () => {
  const [cases, setCases] = useState<any>()

  useEffect(() => {
    getCases().then((response: any) => {
      setCases(response.cases.cases)
    })
  }, [])
  return (
    <div className={styles.container}>
      {cases && (
        <div>
          {cases.map((arrayPart: any) => {
            return arrayPart[1].length > 0 ? (
              <CasesTable cases={arrayPart[1]} key={arrayPart[0]} />
            ) : null
          })}
        </div>
      )}
    </div>
  )
}
