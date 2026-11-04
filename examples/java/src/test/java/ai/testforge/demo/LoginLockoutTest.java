package ai.testforge.demo;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import ai.testforge.demo.pages.LoginPage;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

class LoginLockoutTest {
    private WebDriver driver;
    private LoginPage loginPage;

    @BeforeEach
    void setUp() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless=new", "--no-sandbox", "--disable-dev-shm-usage");
        driver = new ChromeDriver(options);
        loginPage = new LoginPage(driver).openDemo();
    }

    @AfterEach
    void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    void locksDemoAccountAfterFiveFailedAttempts() {
        for (int attempt = 0; attempt < 5; attempt++) {
            loginPage.login("demo", "incorrect-password");
        }

        assertEquals("Account locked for 15 minutes.", loginPage.statusMessage());
        assertTrue(loginPage.loginButtonIsDisabled());
    }
}
