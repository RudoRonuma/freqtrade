param(
    [string]$RemoteName = "official",
    [string]$RemoteBranch = "develop",
    [string]$StartCommit = $null
)


function Get-LastCherryPickedCommit {
    param (
        [string]$FromCommit,
        [int]$MaxDepth = 500
    )
    
    $currentDepth = 0
    if (!$FromCommit) {
        $FromCommit = (& git rev-parse HEAD 2>&1)
    }

    while ($currentDepth -lt $MaxDepth) {
        $currentDepth++
        $targetMessage = (& git log --format=%B -n 1 $FromCommit 2>&1)
        $targetMessage = $targetMessage.Replace("`n", " ")

        # now we should try to see which original commit, this commit
        # been cherry-picked from
        # in the commit message, it should have something like this:
        # (cherry picked from commit <commit-hash>)
        $messageMatches = [regex]::Matches($targetMessage, "cherry picked from commit ([a-f0-9]+)")
        if ($messageMatches.Count -eq 1) {
            $matchedCommit = $messageMatches[0].Groups[1].Value
            if ($matchedCommit) {
                return $matchedCommit
            }
        }

        # Move to the previous commit
        $FromCommit = (& git rev-parse $FromCommit^ 2>&1)
    }

    return $null
}

# If StartCommit is null, get the last commit on the current branch
if (!$StartCommit) {
    $StartCommit = Get-LastCherryPickedCommit
    if (!$StartCommit) {
        throw "Failed to get the last cherry-picked commit, please provide the start commit!"
    }

    Write-Host "Using the last commit on the current branch: $StartCommit" -ForegroundColor Yellow
}
else {
    Write-Host "Using provided start commit: $StartCommit" -ForegroundColor Yellow
}

$futureCommits = (& git rev-list --reverse "$StartCommit..$RemoteName/$RemoteBranch" 2>&1)
if (!$futureCommits) {
    Write-Host "No new commits to cherry-pick, you are all good!" -ForegroundColor Green
    exit 0
}

foreach ($currentCommit in $futureCommits) {
    Write-Host "Cherry-picking commit: $currentCommit"

    # $originalCommitMessage = git log --format=%B -n 1 $currentCommit

    # Prepare the new commit message with the original hash
    # $newMessage = "$originalCommitMessage`n`n(cherry picked from commit $currentCommit)"

    $gitOutput = (& git cherry-pick -x $currentCommit 2>&1)
    Write-Host $gitOutput
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Cherry-pick failed, please resolve the conflicts!" -ForegroundColor Red
        exit 1
    }
    Write-Verbose "Cherry-pick successful: $currentCommit"

    # now we should change the commit message
    # git commit --amend -m $newMessage
}