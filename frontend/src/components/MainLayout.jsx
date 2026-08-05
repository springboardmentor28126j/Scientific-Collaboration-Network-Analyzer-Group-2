import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

function MainLayout({ children }) {

    return (

        <>
            <Navbar />

            <div
                style={{
                    display: "flex",
                    minHeight: "calc(100vh - 70px)",
                    background: "#f5f7fb"
                }}
            >

                <Sidebar />

                <main
                    style={{
                        flex: 1,
                        padding: "30px",
                        overflowY: "auto"
                    }}
                >

                    {children}

                </main>

            </div>

        </>

    );

}

export default MainLayout;