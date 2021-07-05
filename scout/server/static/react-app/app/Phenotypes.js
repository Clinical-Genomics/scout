import React, { useEffect, useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import axios from 'axios'

const useStyles = makeStyles({
  table: {
    minWidth: 650,
  },
});

const Phenotypes = () => {
	const [phenotypes, setPhenotypes] = useState([]);
  const classes = useStyles();

    useEffect(() => {
   axios.get(
        'http://localhost:5000/api/v1/phenotypes',
        {
          withCredentials: true,
          headers: { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' },
        }
      ).then(function (response) {
		   setPhenotypes(response.data.phenotypes)
      }).catch(function (error) {
        // handle error
        console.log(error)
      }).then(function () {
        // always executed
      })
  },[]);

  return (
    <TableContainer component={Paper}>
      <Table className={classes.table} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell align="right">HPO term</TableCell>
            <TableCell align="right">HPO id</TableCell>
            <TableCell align="right">Phenotypes description</TableCell>
            <TableCell align="right">Associated genes</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {phenotypes.map((row) => (
            <TableRow key={row.name}>
              <TableCell align="right">{row.hpo_id}</TableCell>
							<TableCell align="right">{row.hpo_number}</TableCell>
              <TableCell align="right">{row.description}</TableCell>
              <TableCell align="right">{row.genes.length}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default Phenotypes
