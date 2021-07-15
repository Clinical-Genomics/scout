import React from 'react'
import { makeStyles } from '@material-ui/core/styles'
import Table from '@material-ui/core/Table'
import TableBody from '@material-ui/core/TableBody'
import TableCell from '@material-ui/core/TableCell'
import TableContainer from '@material-ui/core/TableContainer'
import TableHead from '@material-ui/core/TableHead'
import TableRow from '@material-ui/core/TableRow'
import Paper from '@material-ui/core/Paper'

const useStyles = makeStyles({
  table: {
    minWidth: 650,
  },
})

interface CasesTableProps {
  cases: any[]
  casesStatus: string
}

export const CasesTable = ({ cases, casesStatus }: CasesTableProps) => {
  const classes = useStyles()
  console.log(cases)
  return (
    <TableContainer component={Paper}>
      <Table className={classes.table} aria-label="cases table">
        <TableHead>
          <TableRow>
            <TableCell>Cases</TableCell>
            <TableCell align="right">Status</TableCell>
            <TableCell align="right">Analysis date</TableCell>
            <TableCell align="right">Link</TableCell>
            <TableCell align="right">Sequencing</TableCell>
            <TableCell align="right">Track</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {cases.map((scoutCase) => (
            <TableRow key={scoutCase.name}>
              <TableCell align="right">{scoutCase.display_name}</TableCell>
              <TableCell align="right">{scoutCase.status}</TableCell>
              <TableCell align="right">{scoutCase.analysis_date}</TableCell>
              <TableCell align="right">{scoutCase.analysis_types.toString()}</TableCell>
              <TableCell align="right">{scoutCase.track}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}
