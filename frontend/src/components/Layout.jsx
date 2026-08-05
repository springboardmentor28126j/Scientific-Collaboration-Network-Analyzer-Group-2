import { Box } from "@mui/material";

function Layout({ children }) {
  return (
    <Box
      sx={{
        padding: 3,
      }}
    >
      {children}
    </Box>
  );
}

export default Layout;