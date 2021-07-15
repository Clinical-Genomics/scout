import React, { useEffect, useState } from 'react'
import { getCases } from '../../mocks/ScoutResponses'
import { CasesTable } from '../../components/CasesTable/CasesTable'

export const CasesPage = () => {
  const [cases, setCases] = useState<any>()

  useEffect(() => {
    setCases(getCases.cases.cases)
  }, [])
  return (
    <div>
      {cases && (
        <div>
          {cases.map((arrayPart: any) => (
            <p>
              <CasesTable cases={arrayPart[1]} casesStatus={arrayPart[0]} key={arrayPart[0]} />
            </p>
          ))}
        </div>
      )}
    </div>
  )
}
