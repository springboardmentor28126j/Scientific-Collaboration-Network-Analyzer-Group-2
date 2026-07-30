import { Box } from "@mui/material";

function Layout({ children }) {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        backgroundColor: "#f5f7fb",
        padding: 3,
      }}
    >
      {children}
    </Box>
  );
}

export default Layout;