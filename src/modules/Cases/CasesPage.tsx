import React, { useEffect, useState } from 'react'
import { CasesTable } from 'components/CasesTable/CasesTable'
import styles from './CasesPage.module.css'

export const CasesPage = () => {
  const [cases, setCases] = useState<any>()

  useEffect(() => {
    fetch('/cases')
      .then((res) => res.json())
      .then((json) => setCases(json.cases[0].getMockCases.cases.cases))
      .catch((err) => console.log(err))
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
