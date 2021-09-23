import React, { useState } from 'react'
import styles from './Phenotypes.module.css'
import { Input, message, Space, Typography } from 'antd'
import { PhenotypesTable } from '../../components/PhenotypesTable/PhenotypesTable'
import { getPhenotypesSearch } from 'services/ScoutApi'
import { ExportCSV } from 'components/ExportCSV/ExportCSV'
import CopyToClipboard from 'components/CopyToClipboard/CopyToClipboard'
import { Loading } from '../../components/Loading/Loading'

const { Search } = Input
const { Text } = Typography
export const PhenotypesPage = () => {
  const [phenotypes, setPhenotypes] = useState<any>()
  const [isLoaded, setIsLoaded] = useState<boolean>(true)
  const onSearch = (value: any) => {
    if (value != '' && value.length > 2) {
      setIsLoaded(false)
      getPhenotypesSearch(value)
        .then((response: any) => {
          setPhenotypes(response.phenotypes)
        })
        .then(() => {
          setIsLoaded(true)
        })
    } else {
      message.error('Search terms must contain at least 3 characters.')
    }
  }
  return (
    <div className={styles.container} data-testid="phenotypes">
      <div className={styles.header} data-testid="test-phenotypes">
        <div className={styles.buttons}>
          <Space size="middle">
            <ExportCSV csvData={phenotypes} fileName={'scout_phenotypes'} />
            <CopyToClipboard copiedData={phenotypes} />
          </Space>
        </div>
        <Search
          placeholder="Search penotypes ..."
          onSearch={onSearch}
          enterButton="Search"
          style={{ width: '30vw' }}
        />
      </div>
      {isLoaded && phenotypes && (
        <div>
          <Text>{`About ${phenotypes.length} ${
            phenotypes.length > 1 ? 'results' : 'result'
          }`}</Text>
        </div>
      )}
      {!isLoaded && <Loading />}
      <PhenotypesTable phenotypes={phenotypes} />
    </div>
  )
}
