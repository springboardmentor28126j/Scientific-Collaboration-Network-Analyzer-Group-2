import { Box } from "@mui/material";
import Sidebar from "./Sidebar";

function Layout({ children }) {

  return (

    <Box
      sx={{
        display: "flex",
        minHeight: "100vh",
        backgroundColor: "#f5f7fb",
      }}
    >

      <Sidebar />

      <Box
        sx={{
          flexGrow: 1,
          padding: 3,
          marginLeft: "260px",
        }}
      >
        {children}
      </Box>

    </Box>

  );

}

export default Layout;