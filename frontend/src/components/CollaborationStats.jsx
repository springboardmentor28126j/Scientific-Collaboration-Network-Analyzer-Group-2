import {
  Grid,
  Card,
  CardContent,
  Typography
} from "@mui/material";

function CollaborationStats({ collaborations = [] }) {

  const total = collaborations.length;

  const pending = collaborations.filter(
    c => c.status === "Pending"
  ).length;

  const active = collaborations.filter(
    c => c.status === "Active"
  ).length;

  const rejected = collaborations.filter(
    c => c.status === "Rejected"
  ).length;

  const cards = [
    {
      title: "Total Collaborations",
      value: total,
      color: "#1976d2"
    },
    {
      title: "Pending",
      value: pending,
      color: "#f9a825"
    },
    {
      title: "Active",
      value: active,
      color: "#2e7d32"
    },
    {
      title: "Rejected",
      value: rejected,
      color: "#d32f2f"
    }
  ];

  return (
    <Grid container spacing={3} mb={4}>
      {cards.map((card) => (
        <Grid item xs={12} sm={6} md={3} key={card.title}>
          <Card
            elevation={6}
            sx={{
              borderTop: `5px solid ${card.color}`,
              borderRadius: 3
            }}
          >
            <CardContent>
              <Typography
                variant="h4"
                fontWeight="bold"
                color={card.color}
              >
                {card.value}
              </Typography>

              <Typography
                variant="subtitle1"
                color="text.secondary"
                mt={1}
              >
                {card.title}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}

export default CollaborationStats;