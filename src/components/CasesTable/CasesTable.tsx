import React from 'react'
import { makeStyles } from '@material-ui/core/styles'
import Table from '@material-ui/core/Table'
import TableBody from '@material-ui/core/TableBody'
import TableCell from '@material-ui/core/TableCell'
import TableContainer from '@material-ui/core/TableContainer'
import TableHead from '@material-ui/core/TableHead'
import TableRow from '@material-ui/core/TableRow'
import Paper from '@material-ui/core/Paper'
import { Chip } from '@material-ui/core'

const useStyles = makeStyles({
  table: {
    minWidth: 650,
  },
})

interface CasesTableProps {
  cases: any[]
}

export const CasesTable = ({ cases }: CasesTableProps) => {
  const classes = useStyles()
  return (
    <TableContainer component={Paper}>
      <Table className={classes.table} aria-label="cases table">
        <TableHead>
          <TableRow>
            <TableCell align="center">Cases</TableCell>
            <TableCell align="center">Status</TableCell>
            <TableCell align="center">Analysis date</TableCell>
            <TableCell align="center">Link</TableCell>
            <TableCell align="center">Sequencing</TableCell>
            <TableCell align="center">Track</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {cases.map((scoutCase) => (
            <TableRow key={scoutCase.display_name}>
              <TableCell align="center">{scoutCase.display_name}</TableCell>
              <TableCell align="center">{scoutCase.status}</TableCell>
              <TableCell align="center">
                {new Date(scoutCase.analysis_date).toISOString().slice(0, 10)}
              </TableCell>
              <TableCell align="center">{scoutCase.link}</TableCell>
              <TableCell align="center">{scoutCase.analysis_types.toString()}</TableCell>
              <TableCell align="center">
                <Chip label={scoutCase.track} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}
