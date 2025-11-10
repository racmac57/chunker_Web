function Invoke-GHGql($q,$v){ (@{query=$q;variables=$v} | ConvertTo-Json -Depth 10) | gh api graphql --input - | ConvertFrom-Json }
