import Chip from "@mui/material/Chip";

function StatusBadge({ status }) {

    let color = "default";

    switch (status) {

        case "Pending":
            color = "warning";
            break;

        case "Accepted":
            color = "success";
            break;

        case "Rejected":
            color = "error";
            break;

        default:
            color = "default";
    }

    return (

        <Chip
            label={status}
            color={color}
            variant="filled"
            size="small"
            sx={{
                fontWeight: "bold",
                minWidth: "90px"
            }}
        />

    );

}

export default StatusBadge;