import {
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography,
    CircularProgress,
    Box
} from "@mui/material";

import StatusBadge from "./StatusBadge";

function CollaborationTable({

    collaborations = [],
    loading = false

}) {

    if (loading) {

        return (

            <Box
                display="flex"
                justifyContent="center"
                mt={5}
            >
                <CircularProgress />
            </Box>

        );

    }

    if (!collaborations.length) {

        return (

            <Paper
                elevation={3}
                sx={{
                    padding: 5,
                    textAlign: "center"
                }}
            >

                <Typography variant="h6">

                    No Collaborations Found

                </Typography>

            </Paper>

        );

    }

    return (

        <TableContainer
            component={Paper}
            elevation={5}
        >

            <Table>

                <TableHead
                    sx={{
                        backgroundColor: "#1976d2"
                    }}
                >

                    <TableRow>

                        <TableCell sx={{ color: "white", fontWeight: "bold" }}>
                            ID
                        </TableCell>

                        <TableCell sx={{ color: "white", fontWeight: "bold" }}>
                            Researcher 1
                        </TableCell>

                        <TableCell sx={{ color: "white", fontWeight: "bold" }}>
                            Researcher 2
                        </TableCell>

                        <TableCell sx={{ color: "white", fontWeight: "bold" }}>
                            Paper
                        </TableCell>

                        <TableCell sx={{ color: "white", fontWeight: "bold" }}>
                            Year
                        </TableCell>

                        <TableCell sx={{ color: "white", fontWeight: "bold" }}>
                            Status
                        </TableCell>

                    </TableRow>

                </TableHead>

                <TableBody>

                    {collaborations.map((item) => (

                        <TableRow
                            key={item.id}
                            hover
                        >

                            <TableCell>{item.id}</TableCell>

                            <TableCell>{item.researcher_1_id}</TableCell>

                            <TableCell>{item.researcher_2_id}</TableCell>

                            <TableCell>{item.paper_id}</TableCell>

                            <TableCell>{item.collaboration_year}</TableCell>

                            <TableCell>

                                <StatusBadge
                                    status={item.status}
                                />

                            </TableCell>

                        </TableRow>

                    ))}

                </TableBody>

            </Table>

        </TableContainer>

    );

}

export default CollaborationTable;