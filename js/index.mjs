import WalletConnect from "@walletconnect/client";
import QRCodeModal from "@walletconnect/qrcode-modal";

console.log(WalletConnect.default)
console.log(QRCodeModal)

async function happyPath() {
  // Create a connector
  const connector = new WalletConnect.default({
    bridge: "https://uniswap.bridge.walletconnect.org", // Required
    qrcodeModal: QRCodeModal
  });

  connector.on("session_update", (error, payload) => {
    if (error) {
      throw error;
    }

    // Get updated accounts and chainId
    const { accounts, chainId } = payload.params[0];
    console.log(accounts, chainId)
  });

  connector.on("disconnect", (error, payload) => {
    if (error) {
      throw error;
    }

    // Delete connector
  });

  const { accounts, chainId } = await connector.connect();
  console.log(accounts, chainId)

  // Draft transaction
  const tx = {
    from: accounts[0], // Required
    to: "0x89D24A7b4cCB1b6fAA2625Fe562bDd9A23260359", // Required (for non contract deployments)
    data: "0x", // Required
    value: "0x10", // Optional
  };

  // Send transaction
  connector
    .sendTransaction(tx)
    .then(result => {
      // Returns transaction id (hash)
      console.log(result);
    })
    .catch(error => {
      // Error returned when rejected
      console.error(error);
    });
}


happyPath()
